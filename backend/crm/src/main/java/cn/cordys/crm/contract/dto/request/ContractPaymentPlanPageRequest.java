package cn.cordys.crm.contract.dto.request;

import cn.cordys.common.dto.BasePageRequest;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 合同回款计划分页入参
 *
 * @author jianxing
 * @date 2025-11-21 15:11:29
 */
@Data
public class ContractPaymentPlanPageRequest extends BasePageRequest {

    @Schema(description = "合同ID")
    private String contractId;

    @Schema(description = "客户ID")
    private String customerId;
}
